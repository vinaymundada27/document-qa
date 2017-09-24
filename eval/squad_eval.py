import argparse
import json
from typing import List

import numpy as np

import trainer
from data_processing.qa_training_data import ParagraphAndQuestionDataset, ContextAndQuestion
from dataset import FixedOrderBatcher
from evaluator import Evaluator, Evaluation, SpanEvaluator
from squad.squad_data import SquadCorpus, split_docs
from model_dir import ModelDir
from utils import transpose_lists, print_table


"""
Run an evalution on squad and record the offical output
"""


class RecordSpanPrediction(Evaluator):
    def __init__(self, bound: int):
        self.bound = bound

    def tensors_needed(self, prediction):
        span, score = prediction.get_best_span(self.bound)
        return dict(spans=span, model_scores=score)

    def evaluate(self, data: List[ContextAndQuestion], true_len, **kargs):
        spans, model_scores = kargs["spans"], kargs["model_scores"]
        results = {"model_conf": model_scores,
                   "predicted_span": spans,
                   "question_id": [x.question_id for x in data]}
        return Evaluation({}, results)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('model', help='name of output to exmaine')
    parser.add_argument("-o", "--official_output", type=str)
    parser.add_argument('-n', '--sample_questions', type=int, default=None)
    parser.add_argument('--answer_bounds', nargs='+', type=int, default=[17])
    parser.add_argument('-b', '--batch_size', type=int, default=200)
    parser.add_argument('-c', '--corpus', choices=["dev", "train"], default="dev")
    parser.add_argument('--ema', action="store_true")
    args = parser.parse_args()

    model_dir = ModelDir(args.model)

    corpus = SquadCorpus()
    if args.corpus == "dev":
        questions = corpus.get_dev()
    else:
        questions = corpus.get_train()
    questions = split_docs(questions)

    if args.sample_questions:
        np.random.RandomState(0).shuffle(sorted(questions, key=lambda x: x.question_id))
        questions = questions[:args.sample_questions]

    dataset = ParagraphAndQuestionDataset(questions, FixedOrderBatcher(args.batch_size, True))

    evaluators = [SpanEvaluator(args.answer_bounds, text_eval="squad")]
    if args.official_output is not None:
        evaluators.append(RecordSpanPrediction(args.answer_bounds[0]))

    checkpoint = model_dir.get_latest_checkpoint()
    evaluation = trainer.test(model_dir.get_model(), evaluators, {args.corpus: dataset},
                              corpus.get_resource_loader(), checkpoint, args.ema)[args.corpus]

    # Print the scalar results in a two column table
    scalars = evaluation.scalars
    cols = list(sorted(scalars.keys()))
    table = [cols]
    header = ["Metric", ""]
    table.append([("%s" % scalars[x] if x in scalars else "-") for x in cols])
    print_table([header] + transpose_lists(table))

    # Save the official output
    if args.official_output is not None:
        quid_to_para = {}
        for x in questions:
            quid_to_para[x.question_id] = x.paragraph

        q_id_to_answers = {}
        q_ids = evaluation.per_sample["question_id"]
        spans = evaluation.per_sample["predicted_span"]
        for q_id, (start, end) in zip(q_ids, spans):
            text = quid_to_para[q_id].get_original_text(start, end)
            q_id_to_answers[q_id] = text

        with open(args.official_output, "w") as f:
            json.dump(q_id_to_answers, f)

if __name__ == "__main__":
    main()
    # tmp()





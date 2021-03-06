from questions.utils.readers import AnnotationReader
from questions.learning.models import DeepLearningModel
from questions.preprocessing.tokenizers import SimpleSpaceTokenizer
from questions.learning.models import Evaluator
from questions.utils.constants import ALL_TYPES

import logging
import numpy as np
import tabulate

import argparse

class Training:
    def __init__(self, data_path, classifier, reader=None, tokenizer=None):
        self.data_path = data_path
        self.classifier = classifier
        if not tokenizer:
            self.tokenizer = SimpleSpaceTokenizer()
        else:
            self.tokenizer = tokenizer
        if not reader:
            self.reader = AnnotationReader(self.data_path, self.tokenizer)
        else:
            self.reader = reader
        self.dataset = self.reader.parse()
        self.logger = logging.getLogger('questions.training')

    def train(self):
        self.logger.info('Training model with the full dataset')
        self.model = self.classifier.train(self.dataset)
        return self.model

    def training_error(self, evaluator=Evaluator(ALL_TYPES)):
        y_true = self.dataset.target()
        y_pred = self.classifier.predict(self.dataset, self.model)
        precision = evaluator.precision(y_true, y_pred)
        recall = evaluator.recall(y_true, y_pred)
        f1_score = evaluator.f1_score(y_true, y_pred)
        return precision, recall, f1_score

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def save(self, model, output_dir):
        model.save(output_dir)

def train(data_path, glove_path, dimensions, output_dir):
    DNN      = DeepLearningModel(glove_path, dimensions)
    trainer  = Training(data_path, DNN)

    model = trainer.train()
    headers = [['Precision', 'Recall', 'F1-Score']]
    precision, recall, f1_score = trainer.training_error()
    row = [[precision, recall, f1_score]]

    table = headers + row
    print
    print tabulate.tabulate(table, headers='firstrow', floatfmt='.3f', tablefmt='pipe')

    trainer.save(model, output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train data')
    parser.add_argument('-d', '--dataset', default='resources/dataset/data.txt',
            help='Path to dataset')
    parser.add_argument('-g', '--glove', default='resources/glove/glove.6B.50d.txt',
            help='Path to Glove vectors')
    parser.add_argument('-n', '--dimensions', type=int, default=50,
            help='Dimensions')
    parser.add_argument('-o', '--output', default='resources/model',
            help='Path to output directory')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    train(args.dataset, args.glove, args.dimensions, args.output)

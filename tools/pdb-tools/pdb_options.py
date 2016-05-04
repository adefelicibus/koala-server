#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_models(dataset_path):
    models_count = 0
    for i, line in enumerate(open(dataset_path)):
        if line.startswith("MODEL"):
            models_count += 1

    return [(i, '%s' % i, False) for i in range(1, models_count + 1)]

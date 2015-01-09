import numpy as np
import sklearn.ensemble

from HPOlibConfigSpace.configuration_space import ConfigurationSpace
from HPOlibConfigSpace.hyperparameters import UniformFloatHyperparameter, \
    UniformIntegerHyperparameter, CategoricalHyperparameter, \
    UnParametrizedHyperparameter, Constant

from ..regression_base import AutoSklearnRegressionAlgorithm


class RandomForest(AutoSklearnRegressionAlgorithm):
    def __init__(self, n_estimators, criterion, max_features,
                 max_depth, min_samples_split, min_samples_leaf,
                 bootstrap,
                 max_leaf_nodes_or_max_depth="max_depth",
                 max_leaf_nodes=None, random_state=None,
                 n_jobs=1):
        self.n_estimators = int(n_estimators)
        if criterion in ("mse",):
            self.criterion = criterion
        else:
            raise ValueError("criterion should be in (mse,) but is: %s" %
                             str(criterion))

        if max_features in ("sqrt", "log2", "auto"):
            raise ValueError("'max_features' should be a float: %s" %
                             str(max_features))
        self.max_features = float(max_features)
        if self.max_features > 1:
            raise ValueError("'max_features' > 1: %s" % str(max_features))

        self.max_leaf_nodes_or_max_depth = str(max_leaf_nodes_or_max_depth)
        if self.max_leaf_nodes_or_max_depth == "max_depth":
            if max_depth == 'None':
                self.max_depth = None
            else:
                self.max_depth = int(max_depth)
            self.max_leaf_nodes = None
        elif self.max_leaf_nodes_or_max_depth == "max_leaf_nodes":
            self.max_depth = None
            if max_leaf_nodes == 'None':
                self.max_leaf_nodes = None
            else:
                self.max_leaf_nodes = int(max_leaf_nodes)
        else:
            raise ValueError("max_leaf_nodes_or_max_depth sould be in "
                             "('max_leaf_nodes', 'max_depth'): %s" %
                             self.max_leaf_nodes_or_max_depth)
        self.min_samples_split = int(min_samples_split)
        self.min_samples_leaf = int(min_samples_leaf)

        if bootstrap == "True":
            self.bootstrap = True
        else:
            self.bootstrap = False

        self.random_state = random_state
        self.n_jobs = n_jobs
        self.estimator = None

    def fit(self, X, Y):
        self.estimator = sklearn.ensemble.RandomForestRegressor(
            n_estimators=self.n_estimators,
            criterion=self.criterion,
            max_features=self.max_features,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            bootstrap=self.bootstrap,
            max_leaf_nodes=self.max_leaf_nodes,
            random_state=self.random_state,
            n_jobs=self.n_jobs)
        return self.estimator.fit(X, Y)

    def predict(self, X):
        if self.estimator is None:
            raise NotImplementedError
        return self.estimator.predict(X)

    @staticmethod
    def get_properties():
        return {'shortname': 'RF',
                'name': 'Random Forest Regressor',
                'handles_missing_values': False,
                'handles_nominal_values': False,
                'handles_numerical_features': True,
                'prefers_data_scaled': False,
                # TODO find out if this is good because of sparcity...
                'prefers_data_normalized': False,
                'is_deterministic': True,
                'handles_sparse': False,
                # TODO find out what is best used here!
                # But rather fortran or C-contiguous?
                'preferred_dtype': np.float32}

    @staticmethod
    def get_hyperparameter_search_space():
        criterion = Constant(name="criterion", value="mse")
        # Copied from classification/random_forest.py
        n_estimators = UniformIntegerHyperparameter(
            name="n_estimators", lower=10, upper=100, default=10, log=False)
        max_features = UniformFloatHyperparameter(
            name="max_features", lower=0.01, upper=0.5, default=0.1)
        max_depth = UnParametrizedHyperparameter("max_depth", "None")
        min_samples_split = UniformIntegerHyperparameter(
            name="min_samples_split", lower=2, upper=20, default=2, log=False)
        min_samples_leaf = UniformIntegerHyperparameter(
            name="min_samples_leaf", lower=1, upper=20, default=1, log=False)
        bootstrap = CategoricalHyperparameter(
            name="bootstrap", choices=["True", "False"], default="True")

        cs = ConfigurationSpace()
        cs.add_hyperparameter(n_estimators)
        cs.add_hyperparameter(max_features)
        cs.add_hyperparameter(max_depth)
        cs.add_hyperparameter(min_samples_split)
        cs.add_hyperparameter(min_samples_leaf)
        cs.add_hyperparameter(bootstrap)
        cs.add_hyperparameter(criterion)

        return cs

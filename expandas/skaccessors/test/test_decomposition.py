#!/usr/bin/env python

import numpy as np
import pandas as pd
import pandas.compat as compat

import sklearn.datasets as datasets
import sklearn.decomposition as decomposition

import expandas as expd
import expandas.util.testing as tm


class TestDecomposition(tm.TestCase):

    def test_objectmapper(self):
        df = expd.ModelFrame([])
        self.assertIs(df.decomposition.PCA, decomposition.PCA)
        self.assertIs(df.decomposition.ProjectedGradientNMF, decomposition.ProjectedGradientNMF)
        self.assertIs(df.decomposition.RandomizedPCA, decomposition.RandomizedPCA)
        self.assertIs(df.decomposition.KernelPCA, decomposition.KernelPCA)
        self.assertIs(df.decomposition.FactorAnalysis, decomposition.FactorAnalysis)
        self.assertIs(df.decomposition.FastICA, decomposition.FastICA)
        self.assertIs(df.decomposition.TruncatedSVD, decomposition.TruncatedSVD)
        self.assertIs(df.decomposition.NMF, decomposition.NMF)
        self.assertIs(df.decomposition.SparsePCA, decomposition.SparsePCA)
        self.assertIs(df.decomposition.MiniBatchSparsePCA, decomposition.MiniBatchSparsePCA)
        self.assertIs(df.decomposition.SparseCoder, decomposition.SparseCoder)
        self.assertIs(df.decomposition.DictionaryLearning, decomposition.DictionaryLearning)
        self.assertIs(df.decomposition.MiniBatchDictionaryLearning, decomposition.MiniBatchDictionaryLearning)

    def test_fastica(self):
        iris = datasets.load_iris()
        df = expd.ModelFrame(iris)

        result = df.decomposition.fastica(random_state=self.random_state)
        expected = decomposition.fastica(iris.data, random_state=self.random_state)

        self.assertEqual(len(result), 3)
        self.assertTrue(isinstance(result[0], pd.DataFrame))
        self.assert_index_equal(result[0].index, df.data.columns)
        self.assert_numpy_array_almost_equal(result[0].values, expected[0])

        self.assertTrue(isinstance(result[1], pd.DataFrame))
        self.assert_numpy_array_almost_equal(result[1].values, expected[1])

        self.assertTrue(isinstance(result[2], pd.DataFrame))
        self.assert_index_equal(result[2].index, df.index)
        self.assert_numpy_array_almost_equal(result[2].values, expected[2])

        result = df.decomposition.fastica(return_X_mean=True, random_state=self.random_state)
        expected = decomposition.fastica(iris.data, return_X_mean=True,
                                         random_state=self.random_state)

        self.assertEqual(len(result), 4)
        self.assertTrue(isinstance(result[0], pd.DataFrame))
        self.assert_index_equal(result[0].index, df.data.columns)
        self.assert_numpy_array_almost_equal(result[0].values, expected[0])

        self.assertTrue(isinstance(result[1], pd.DataFrame))
        self.assert_numpy_array_almost_equal(result[1].values, expected[1])

        self.assertTrue(isinstance(result[2], pd.DataFrame))
        self.assert_index_equal(result[2].index, df.index)
        self.assert_numpy_array_almost_equal(result[2].values, expected[2])

        self.assert_numpy_array_almost_equal(result[3], expected[3])

    def test_dict_learning(self):
        iris = datasets.load_iris()
        df = expd.ModelFrame(iris)

        result = df.decomposition.dict_learning(2, 1, random_state=self.random_state)
        expected = decomposition.dict_learning(iris.data, 2, 1,
                                               random_state=self.random_state)
        self.assertEqual(len(result), 3)
        self.assertTrue(isinstance(result[0], pd.DataFrame))
        self.assert_index_equal(result[0].index, df.data.index)
        self.assert_numpy_array_almost_equal(result[0].values, expected[0])

        self.assertTrue(isinstance(result[1], pd.DataFrame))
        self.assert_index_equal(result[1].columns, df.data.columns)
        self.assert_numpy_array_almost_equal(result[1].values, expected[1])

        self.assert_numpy_array_almost_equal(result[2], expected[2])

    def test_dict_learning_online(self):
        iris = datasets.load_iris()
        df = expd.ModelFrame(iris)

        result = df.decomposition.dict_learning_online(random_state=self.random_state)
        expected = decomposition.dict_learning_online(iris.data,
                                                      random_state=self.random_state)

        self.assertEqual(len(result), 2)
        self.assertTrue(isinstance(result[0], pd.DataFrame))
        self.assert_index_equal(result[0].index, df.data.index)
        self.assert_numpy_array_almost_equal(result[0].values, expected[0])

        self.assertTrue(isinstance(result[1], pd.DataFrame))
        self.assert_index_equal(result[1].columns, df.data.columns)
        self.assert_numpy_array_almost_equal(result[1].values, expected[1])

        result = df.decomposition.dict_learning_online(return_code=False,
                                                       random_state=self.random_state)
        expected = decomposition.dict_learning_online(iris.data,
                                                      return_code=False,
                                                      random_state=self.random_state)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assert_index_equal(result.columns, df.data.columns)
        self.assert_numpy_array_almost_equal(result.values, expected)

    def test_sparse_encode(self):
        iris = datasets.load_iris()
        df = expd.ModelFrame(iris)

        _, dictionary, _ = decomposition.dict_learning(iris.data, 2, 1,
                                                       random_state=self.random_state)

        result = df.decomposition.sparse_encode(dictionary)
        expected = decomposition.sparse_encode(iris.data, dictionary)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assert_index_equal(result.index, df.data.index)
        self.assert_numpy_array_almost_equal(result.values, expected)

    def test_Decompositions(self):
        iris = datasets.load_iris()
        df = expd.ModelFrame(iris)

        models = ['PCA', 'KernelPCA']
        for model in models:
            mod1 = getattr(df.decomposition, model)()
            mod2 = getattr(decomposition, model)()

            df.fit(mod1)
            mod2.fit(iris.data, iris.target)

            result = df.transform(mod1)
            expected = mod2.transform(iris.data)

            self.assertTrue(isinstance(result, expd.ModelFrame))
            self.assert_series_equal(df.target, result.target)
            self.assert_numpy_array_almost_equal(result.data.values, expected)


    def test_fit_transform(self):
        iris = datasets.load_iris()
        df = expd.ModelFrame(iris)

        models = ['PCA', 'KernelPCA']
        for model in models:
            mod1 = getattr(df.decomposition, model)()
            mod2 = getattr(decomposition, model)()

            result = df.fit_transform(mod1)
            expected = mod2.fit_transform(iris.data, iris.target)

            self.assertTrue(isinstance(result, expd.ModelFrame))
            self.assert_series_equal(df.target, result.target)
            self.assert_numpy_array_almost_equal(result.data.values, expected)


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb', '--pdb-failure'],
                   exit=False)
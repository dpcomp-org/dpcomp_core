import json
from dpcomp_core import cartesian_product
from dpcomp_core.algorithm import uniform
from dpcomp_core.execution import assemble_experiments
from dpcomp_core.execution import FileWriter
from dpcomp_core.execution import ListWriter
from dpcomp_core.execution import process_experiments
from dpcomp_core import dataset
from dpcomp_core import experiment
from dpcomp_core import metric
from dpcomp_core import workload
from dpcomp_core import util
import mock
import unittest


class TestExecution(unittest.TestCase):

    def setUp(self):
        A = uniform.uniform_noisy_engine()
        X = dataset.DatasetSampledFromFile(nickname='BIDS-ALL', 
                                           sample_to_scale=1E4, 
                                           reduce_to_dom_shape=1024, 
                                           seed=0)
        W = workload.Prefix1D(domain_shape_int=1024)
        E1 = experiment.Single(X, W, A, 0.1, 0)
        E2 = experiment.Single(X, W, A, 0.1, 1)
        self.metric_group = [metric.SampleError(E1), metric.SampleError(E2)]

    def test_list_writer(self):
        writer = ListWriter()
        writer.write(self.metric_group)
        writer.close()

        self.assertEqual(writer.metric_groups.pop(), self.metric_group)
        
    def test_file_writer(self):
        fd = mock.MagicMock()
        writer = FileWriter(fd)

        writer.write(self.metric_group)

        prepared_m1 = util.prepare_for_json(self.metric_group[0].asDict())
        prepared_m2 = util.prepare_for_json(self.metric_group[1].asDict())

        fd.write.assert_called_with(json.dumps([prepared_m1, prepared_m2]))

    def test_process_experiments(self):
        writer = ListWriter()
        cartesian_product.run = mock.MagicMock()
        params = mock.MagicMock()
        params_map = {'x': [params]}

        process_experiments(params_map, writer)    

        cartesian_product.run.assert_called_with(params)

    def test_assemble_experiments(self):
        cartesian_product.cartesian_product = mock.MagicMock()

        algorithms = {1: mock.MagicMock()}
        datasets = {mock.MagicMock(): 1}
        workloads = {1: workload.Prefix1D}
        domains = {1: mock.MagicMock()}
        epsilons = {1: mock.MagicMock()}
        scales = {1: mock.MagicMock()}
        query_sizes = [mock.MagicMock()]
        ex = mock.MagicMock()
        ex_seeds = [ex]
        ds = mock.MagicMock()
        ds_seeds = [ds]

        params = (ex, datasets, domains, algorithms, epsilons, scales, query_sizes, workloads, ds)
    
        assemble_experiments(algorithms, 
                             datasets, 
                             workloads,
                             domains, 
                             epsilons, 
                             scales, 
                             query_sizes, 
                             ex_seeds, 
                             ds_seeds)

        cartesian_product.cartesian_product.assert_called_with(*params)

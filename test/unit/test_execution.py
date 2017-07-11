import json
from dpcomp_core import cartesian_product
from dpcomp_core.execution import assemble_experiments
from dpcomp_core.execution import FileWriter
from dpcomp_core.execution import ListWriter
from dpcomp_core.execution import process_experiments
from dpcomp_core import workload
import mock
import unittest


class TestExecution(unittest.TestCase):

    def setUp(self):
        self.metric_group = ['m1', 'm2']

    def test_list_writer(self):
        writer = ListWriter()
        writer.write(self.metric_group)
        writer.close()

        self.assertEqual(sorted(writer.metric_groups.pop()), 
                         sorted(self.metric_group))
        
    def test_file_writer(self):
        fd = mock.MagicMock()
        writer = FileWriter(fd)

        writer.write(self.metric_group)
        fd.write.assert_called_with(json.dumps(self.metric_group))

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

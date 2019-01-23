# comments on test layout: https://docs.pytest.org/en/latest/goodpractices.html
# run with python -m unittest tests.test_fenicsadapter

from unittest.mock import MagicMock, patch
from unittest import TestCase
import warnings

fake_dolfin = MagicMock()
fake_PySolverInterface = MagicMock()


@patch.dict('sys.modules', **{'PySolverInterface': fake_PySolverInterface, 'dolfin': fake_dolfin})
class MyTest(TestCase):
    dummy_config = "tests/precice-adapter-config.json"

    def setUp(self):
        fake_PySolverInterface.PyActionReadIterationCheckpoint = MagicMock(return_value=1)
        fake_PySolverInterface.PyActionWriteIterationCheckpoint = MagicMock(return_value=2)
        warnings.simplefilter('ignore', category=ImportWarning)

    @patch('PySolverInterface.PySolverInterface')
    def test_advance_success(self, fake_PySolverInterface_PySolverInterface):
        import PySolverInterface

        readIterationCheckpointOut = False
        desiredOutputOfAdvance = not readIterationCheckpointOut

        def mock_feedback(input):
            if input == PySolverInterface.PyActionReadIterationCheckpoint():
                return readIterationCheckpointOut
            elif input == PySolverInterface.PyActionWriteIterationCheckpoint():
                return (not readIterationCheckpointOut)

        fake_PySolverInterface_PySolverInterface.return_value.isActionRequired = MagicMock(side_effect=mock_feedback)
        fake_PySolverInterface_PySolverInterface.return_value.writeBlockScalarData = MagicMock()
        fake_PySolverInterface_PySolverInterface.return_value.readBlockScalarData = MagicMock()
        fake_PySolverInterface_PySolverInterface.return_value.advance = MagicMock()

        import fenicsadapter
        precice = fenicsadapter.Adapter(self.dummy_config)
        precice.extract_coupling_boundary_coordinates = MagicMock(return_value=(None, None))
        precice.convert_fenics_to_precice = MagicMock()
        precice._coupling_bc_expression = MagicMock()
        precice._coupling_bc_expression.update_boundary_data = MagicMock()

        self.assertEqual(precice.advance(None,0), desiredOutputOfAdvance)
        return 0

    @patch('PySolverInterface.PySolverInterface')
    def test_advance_rollback(self,fake_PySolverInterface_PySolverInterface):
        import PySolverInterface

        readIterationCheckpointOut = True
        desiredOutputOfAdvance = not readIterationCheckpointOut

        def mock_feedback(input):
            if input == PySolverInterface.PyActionReadIterationCheckpoint():
                return readIterationCheckpointOut
            elif input == PySolverInterface.PyActionWriteIterationCheckpoint():
                return (not readIterationCheckpointOut)

        fake_PySolverInterface_PySolverInterface.return_value.isActionRequired = MagicMock(side_effect=mock_feedback)
        fake_PySolverInterface_PySolverInterface.return_value.writeBlockScalarData = MagicMock()
        fake_PySolverInterface_PySolverInterface.return_value.readBlockScalarData = MagicMock()
        fake_PySolverInterface_PySolverInterface.return_value.advance = MagicMock()

        import fenicsadapter
        precice = fenicsadapter.Adapter(self.dummy_config)
        precice.extract_coupling_boundary_coordinates = MagicMock(return_value=(None, None))
        precice.convert_fenics_to_precice = MagicMock()
        precice._coupling_bc_expression = MagicMock()
        precice._coupling_bc_expression.update_boundary_data = MagicMock()

        self.assertEqual(precice.advance(None,0), desiredOutputOfAdvance)

    @patch('PySolverInterface.PySolverInterface')
    def test_isCouplingOngoing(self,fake_PySolverInterface_PySolverInterface):
        import fenicsadapter
        precice = fenicsadapter.Adapter(self.dummy_config)

        fake_PySolverInterface_PySolverInterface.return_value.isCouplingOngoing = MagicMock(return_value=True)
        self.assertEqual(precice.is_coupling_ongoing(), True)

        fake_PySolverInterface_PySolverInterface.return_value.isCouplingOngoing = MagicMock(return_value=False)
        self.assertEqual(precice.is_coupling_ongoing(), False)
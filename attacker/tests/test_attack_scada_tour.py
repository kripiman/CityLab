import os
import tempfile
import threading
import unittest
from pathlib import Path

from attacker.attack_scada_tour import ScadaTour, main as tour_main
from network.historian import HistorianTSDB
from network.hmi_server import IndustrialHmiEngine, ThreadedHmiServer, HmiRequestHandler


class TestScadaTour(unittest.TestCase):

    def test_scada_tour_engine_direct(self) -> None:
        """Verifica la exploración directa sobre el motor HMI."""
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        db_path = Path(temp_db.name)
        self.addCleanup(self._cleanup_db, str(db_path))

        historian = HistorianTSDB(db_path=db_path)
        self.addCleanup(historian.close)
        
        engine = IndustrialHmiEngine(historian=historian)
        tour = ScadaTour()
        res = tour.run_scada_exploration(engine=engine)
        
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'ENGINE_DIRECT')
        self.assertTrue(res['overview_retrieved'])
        self.assertIn('water_sector', res['sectors'])

    def test_scada_tour_live_http_socket(self) -> None:
        """Verifica la consulta HTTP contra el servidor HMI real en puerto alto."""
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        db_path = Path(temp_db.name)
        self.addCleanup(self._cleanup_db, str(db_path))

        historian = HistorianTSDB(db_path=db_path)
        self.addCleanup(historian.close)

        engine = IndustrialHmiEngine(historian=historian)
        HmiRequestHandler.engine = engine
        server = ThreadedHmiServer(('127.0.0.1', 18085), HmiRequestHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.shutdown)
        self.addCleanup(server.server_close)

        tour = ScadaTour()
        res = tour.run_scada_exploration(hmi_url="http://127.0.0.1:18085")

        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['mode'], 'SOCKET_LIVE')
        self.assertTrue(res['overview_retrieved'])
        self.assertIn('water_sector', res['sectors'])

    def test_scada_tour_cli(self) -> None:
        """Verifica la invocación CLI."""
        rc = tour_main(['--url', 'http://127.0.0.1:59997'])
        self.assertEqual(rc, 0)

    @staticmethod
    def _cleanup_db(db_path: str) -> None:
        import os
        for ext in ('', '-wal', '-shm'):
            p = db_path + ext
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


if __name__ == '__main__':
    unittest.main()

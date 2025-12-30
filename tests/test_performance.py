import time
import pandas as pd
import numpy as np
from datalint.engine.validators import run_all_validations

class TestPerformance:
    def test_large_dataset_performance(self):
        # Generate 100K row dataset
        np.random.seed(42)
        df = pd.DataFrame({
            'numeric1': np.random.randn(100000),
            'numeric2': np.random.randn(100000),
            'categorical': np.random.choice(['A', 'B', 'C'], 100000)
        })

        start_time = time.time()
        results = run_all_validations(df, threshold=0.05)
        end_time = time.time()

        # Should complete in under 10 seconds
        assert end_time - start_time < 10.0
        assert all(r['passed'] for r in results.values())
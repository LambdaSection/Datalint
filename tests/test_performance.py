"""
Performance tests for DataLint validators.
"""

import time
import pandas as pd
import numpy as np
from datalint.engine.base import ValidationRunner
from datalint.engine.validators import get_default_validators


class TestPerformance:
    def test_large_dataset_performance(self):
        """Test that validation completes quickly on large datasets."""
        # Generate 100K row dataset
        np.random.seed(42)
        df = pd.DataFrame({
            'numeric1': np.random.randn(100000),
            'numeric2': np.random.randn(100000),
            'categorical': np.random.choice(['A', 'B', 'C'], 100000)
        })

        validators = get_default_validators()
        runner = ValidationRunner(validators)

        start_time = time.time()
        results = runner.run(df)
        end_time = time.time()

        # Should complete in under 10 seconds
        assert end_time - start_time < 10.0
        assert all(r.passed for r in results)
from NetworkSecurity.pipeline.training_pipeline import TrainingPipeline


def test_training_pipeline_can_be_constructed():
    pipeline = TrainingPipeline()

    assert pipeline.training_pipeline_config is not None

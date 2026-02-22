"""MLflow logging stubs."""


def log_run(run_data: dict):
    # Stub: in real usage, wrap with mlflow.start_run and log artifacts
    try:
        # Placeholder for actual logging
        print("MLflow stub log:", run_data.get("url"))
    except Exception:
        pass

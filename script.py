from dymaxionlabs.model import Estimator, Project
import time


def main():
    # Predict with a local file
    model = Estimator('b4676699-27c8-4193-a24c-cffaf88cce92')

    job = model.predict(local_files=['img.jpg'])

    while not job.status():
        print("Waiting for results...")
        time.sleep(60)

    job.download_results("./results")

    # Predict with uploaded files
    project = Project()
    files = project.files()

    job2 = model.predict(preload_files=[files[0].name])

    while not job2.status():
        print("Waiting for seconds results...")
        time.sleep(60)

    job2.download_results("./results")


if __name__ == "__main__":
    main()

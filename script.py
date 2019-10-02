from src.terra.model import Estimator
import time


def main():
    model = Estimator('b4676699-27c8-4193-a24c-cffaf88cce92')

    job = model.predict(['img.jpg'])

    while not job.status():
        print("Waiting for results...")
        time.sleep(60)

    job.download_results("./results")


if __name__ == "__main__":
    main()

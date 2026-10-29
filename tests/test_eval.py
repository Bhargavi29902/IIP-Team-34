from eval.run_eval import THRESHOLD, evaluate


def test_extraction_accuracy_does_not_drop(app):
    report = evaluate()
    assert report["overall"] >= THRESHOLD, report

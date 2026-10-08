import argparse
from .schema import load_scenario
from .runner import EvaluationRunner, FixtureAgent, save_report

def main():
    p = argparse.ArgumentParser(description="Run a deterministic DeerFlow evaluation scenario")
    p.add_argument("command", choices=["run"])
    p.add_argument("scenario")
    p.add_argument("--output", default="out")
    args = p.parse_args()
    report = EvaluationRunner(FixtureAgent()).run(load_scenario(args.scenario))
    path = save_report(report, args.output)
    print(f"case={report.case_id} release_pass={report.release_pass} report={path}")
    for s in report.scores:
        print(f"  {s.metric}: {s.status} ({s.score}) - {s.reason}")
    raise SystemExit(0 if report.release_pass else 1)

if __name__ == "__main__":
    main()

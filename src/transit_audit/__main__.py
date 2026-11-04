import argparse
from .demo import run_demo


def main():
    parser = argparse.ArgumentParser(description="Transit forecast audit research seed")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Run the explicitly synthetic demonstration")
    demo.add_argument("--output", required=True)
    demo.add_argument("--seed", type=int, default=2000)
    args = parser.parse_args()
    if args.command == "demo":
        result = run_demo(args.output, args.seed)
        print(result["warning"])
        print(f"Wrote {result['timings']} synthetic forecast scores to {args.output}")


if __name__ == "__main__":
    main()

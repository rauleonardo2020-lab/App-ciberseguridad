import sys, json

def main():
    try:
        data = json.load(sys.stdin)
        tok = data.get("access_token")
        if not tok:
            print("")
            return 1
        print(tok)
        return 0
    except Exception:
        print("")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

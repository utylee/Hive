from hive import remote


def main() -> None:
    result = remote.exec("m5", "hostname")
    print(result.stdout.strip())


if __name__ == "__main__":
    main()

ROOT = {
    "hosts": [
        "Root CA",
    ],
    "key": {"algo": "rsa", "size": 4096},
    "names": [
        {
            "C": "AT",
            "L": "Lab",
            "O": "not a productive CA",
            "OU": "WWW",
            "ST": "Internet",
        }
    ],
}
LEAF = {
        "key": {"algo": "rsa", "size": 2048},
        "names": [
            {
                "C": "AT",
                "L": "Innsbruck",
                "O": "Sauerwein Solutions",
                "OU": "Sauerwein",
                "ST": "Tyrol",
            }
        ],
    }

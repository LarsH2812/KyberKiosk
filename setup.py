import sys
from cx_Freeze import setup, Executable


base = "Win32GUI" if sys.platform == "win32" else None
    

directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
]

msi_data = {
    "ProgId":[
        ("Prog.Id", None, None, "De enige echte KyberKiosk", "IconId", None),
    ],
    "Icon":[
        ("IconId", "KyberKiosk.ico"),
    ],
}

bdist_msi_options = {
    "summary_data":{
        "author": "Lars Hartman"
    },
    "all_users": True,
    "install_icon": "KyberKiosk.ico",
    "data": msi_data,
    "environment_variables":[
        ("E_KyberKiosk_VAR","=-*KyberKiosk_VAR", "1", "TARGETDIR")
    ],
    "directories": directory_table,
}

build_exe_options = {
    "include_files":{
        "KyberKiosk.sqlite",
        "QRcode.svg",
        "style.qss"
    },
    "include_msvcr": True
}

executables = (
    [
        Executable(
            "main.py",
            target_name="KyberKiosk",
            base=base,
            copyright="Copyright (C) 2022 Lars Hartman",
            icon = "KyberKiosk.ico",
        )
    ]
)

setup(  name = "KyberKiosk",
        version = "1.2",
        description = "De enige echte KyberKiosk",
        executables=executables,
        options = {
            "build_exe":build_exe_options,
            "bdist_msi":bdist_msi_options
        }
    )

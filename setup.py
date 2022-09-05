import sys
from cx_Freeze import setup, Executable


base = "Win32GUI" if sys.platform == "win32" else None
path = sys.path
    

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
    "upgrade_code": "{309b2e34-2c2a-404b-a082-c1a0bebddbe4}",
}

build_exe_options = {
    "include_files":{
        "KyberKiosk.sqlite",
        "QRcode.svg",
        "style.qss"
    },
    "bin_path_includes": path,
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
        version = "1.4",
        description = """
        De enige echte KyberKiosk
        
        Version update to 1.4:
            -Changed how the change user details screen handles the double qr check, so it doesnt throw a false positive.
        Version update to 1.3:
            -Changed how the QR login works, so that it should not disrupt the workflow!""",
        executables=executables,
        options = {
            "build_exe":build_exe_options,
            "bdist_msi":bdist_msi_options
        }
    )

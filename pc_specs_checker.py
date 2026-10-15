import platform
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

import psutil


APP_NAME = "PC Specs Checker"


def run_powershell(command):
    """Run a PowerShell command and return its output, or an empty string."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def get_cpu_name():
    name = platform.processor().strip()
    if name and name.lower() not in {"unknown", "none"}:
        return name

    # Windows fallback for systems where platform.processor() is blank.
    return run_powershell(
        "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)"
    ) or "Tidak diketahui"


def get_gpu_names():
    output = run_powershell(
        "Get-CimInstance Win32_VideoController | "
        "Select-Object -ExpandProperty Name"
    )
    if not output:
        return ["Tidak dapat dibaca oleh Windows"]
    return [line.strip() for line in output.splitlines() if line.strip()]


def format_bytes(num_bytes):
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:,.2f} {unit}"
        value /= 1024
    return f"{value:,.2f} TB"


def get_disk_info():
    lines = []
    seen_devices = set()

    for partition in psutil.disk_partitions(all=False):
        # Ignore partitions that Windows cannot currently access.
        if not partition.device or partition.device in seen_devices:
            continue
        seen_devices.add(partition.device)
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            lines.append(
                f"{partition.device}  |  Total: {format_bytes(usage.total)}"
                f"  |  Used: {format_bytes(usage.used)}"
                f"  |  Free: {format_bytes(usage.free)}"
                f"  |  Usage: {usage.percent}%"
            )
        except (PermissionError, OSError):
            lines.append(f"{partition.device}  |  Tidak dapat diakses")
    return lines or ["Tidak ada disk yang dapat dibaca"]


def collect_specs():
    memory = psutil.virtual_memory()
    cpu_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)

    try:
        cpu_usage = psutil.cpu_percent(interval=1)
    except Exception:
        cpu_usage = None

    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError, OverflowError):
        boot_time = "Tidak diketahui"

    lines = [
        f"{APP_NAME}",
        "=" * 60,
        f"Waktu pemeriksaan : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "SISTEM",
        f"OS                 : {platform.system()} {platform.release()}",
        f"Versi OS           : {platform.version()}",
        f"Arsitektur         : {platform.machine()}",
        f"Nama komputer      : {platform.node()}",
        f"Waktu boot         : {boot_time}",
        "",
        "PROSESOR",
        f"CPU                : {get_cpu_name()}",
        f"Core fisik         : {cpu_cores if cpu_cores is not None else 'Tidak diketahui'}",
        f"Core logis         : {logical_cores if logical_cores is not None else 'Tidak diketahui'}",
        f"Penggunaan CPU     : {cpu_usage if cpu_usage is not None else 'Tidak tersedia'}"
        + ("%" if cpu_usage is not None else ""),
        "",
        "MEMORI (RAM)",
        f"RAM total          : {format_bytes(memory.total)}",
        f"RAM digunakan     : {format_bytes(memory.used)}",
        f"RAM tersedia      : {format_bytes(memory.available)}",
        f"Penggunaan RAM     : {memory.percent}%",
        "",
        "KARTU GRAFIS",
    ]

    lines.extend(f"GPU {index}: {name}" for index, name in enumerate(get_gpu_names(), start=1))
    lines.extend(["", "PENYIMPANAN"])
    lines.extend(get_disk_info())
    lines.extend([
        "",
        "Catatan: Informasi GPU yang ditampilkan berasal dari Windows dan mungkin",
        "tidak mencakup seluruh detail seperti VRAM khusus pada setiap perangkat.",
        "=" * 60,
    ])
    return "\n".join(lines)


def main():
    while True:
        print("\n" + "=" * 44)
        print("       PC SPECS CHECKER")
        print("=" * 44)
        print("1. Lihat spesifikasi komputer")
        print("2. Simpan spesifikasi ke file TXT")
        print("3. Keluar")

        choice = input("\nPilih menu (1-3): ").strip()

        if choice == "1":
            print("\n" + collect_specs())
            input("\nTekan Enter untuk kembali ke menu...")
        elif choice == "2":
            report = collect_specs()
            filename = f"pc_specs_{datetime.now():%Y%m%d_%H%M%S}.txt"
            output_path = Path.cwd() / filename
            try:
                output_path.write_text(report, encoding="utf-8")
                print(f"\nLaporan berhasil disimpan:\n{output_path}")
            except OSError as error:
                print(f"\nGagal menyimpan laporan: {error}")
            input("\nTekan Enter untuk kembali ke menu...")
        elif choice == "3":
            print("Terima kasih telah menggunakan PC Specs Checker!")
            break
        else:
            print("Pilihan tidak valid. Masukkan 1, 2, atau 3.")


if __name__ == "__main__":
    main()

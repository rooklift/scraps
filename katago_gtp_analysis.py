import subprocess
import sys

katago_path = "C:/Programs (self-installed)/KataGo 1.15.3 CUDA/katago.exe"
model_path = "C:/Users/Owner/Documents/Misc/KataGo/kata1-b18c384nbt-s9996604416-d4316597426.bin.gz"

# Test moves
moves = [
    "B Q16", "W D17", "B Q3", "W C4", "B E4", "W R5", "B Q7", "W M3", "B Q5", "W J3", "B R6", "W D6", "B D15", "W F17",
]

def start_katago():

    # Command to start KataGo in GTP mode
    command = [katago_path, "gtp", "-model", model_path]

    try:
        # Start KataGo process with pipe for stdin, stdout, and stderr
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )

        print("KataGo started successfully!")
        return process
    except Exception as e:
        print(f"Error starting KataGo: {e}")
        sys.exit(1)

def send_command(process, command, cmd_id):
    """Send a GTP command to KataGo and print the response."""
    # Add the command ID
    cmd_with_id = f"{cmd_id} {command}"
    print(f"\nSending: {cmd_with_id}")

    # Send command to KataGo
    process.stdin.write(cmd_with_id + "\n")
    process.stdin.flush()

    # Read response
    response = []
    line = process.stdout.readline().strip()

    # GTP responses begin with either '=' or '?' followed by the command ID
    while line and not (line.startswith(f"={cmd_id}") or line.startswith(f"?{cmd_id}")):
        line = process.stdout.readline().strip()

    # First line of the actual response
    response.append(line)

    # Read until we get an empty line (GTP responses end with an empty line)
    line = process.stdout.readline().strip()
    while line:
        response.append(line)
        line = process.stdout.readline().strip()

    print("Response:")
    for r in response:
        print(r)

    return response

def send_analysis_command(process, cmd_id, max_updates=4):
    """
    Send analysis command and capture a specified number of analysis updates.
    """
    # Send the analysis command
    analysis_cmd = f"{cmd_id} kata-analyze interval 50 rootInfo true"
    print(f"\nSending: {analysis_cmd}")

    process.stdin.write(analysis_cmd + "\n")
    process.stdin.flush()

    # Wait for initial response with our command ID
    line = process.stdout.readline().strip()
    while not (line.startswith(f"={cmd_id}") or line.startswith(f"?{cmd_id}")):
        line = process.stdout.readline().strip()

    print(f"Initial analysis response: {line}")

    # Collect specified number of analysis updates
    update_count = 0
    while update_count < max_updates:
        line = process.stdout.readline().strip()
        if line:  # Skip empty lines
            print(f"Received analysis line {update_count + 1}")
            update_count += 1

    return update_count

def main():
    # Start KataGo process
    katago_process = start_katago()
    cmd_counter = 1

    try:
        # Basic test - send a name command
        send_command(katago_process, "name", cmd_counter)
        cmd_counter += 1

        # Process test moves
        for i, move in enumerate(moves):
            # Send play command for current move
            play_cmd = f"play {move}"
            send_command(katago_process, play_cmd, cmd_counter)
            cmd_counter += 1

            # Send analysis command and collect updates
            updates = send_analysis_command(katago_process, cmd_counter, max_updates=4)
            cmd_counter += 1

            # For the last move, we need to explicitly send a command to stop analysis
            if i == len(moves) - 1:
                send_command(katago_process, "name", cmd_counter)
                cmd_counter += 1

        # Clean shutdown
        send_command(katago_process, "quit", cmd_counter)
    finally:
        # Make sure to clean up the process
        katago_process.terminate()
        print("KataGo process terminated.")

if __name__ == "__main__":
    main()
import io
import selectors
import subprocess
import sys

def capture_subprocess_output(subprocess_args, process_line=None):
    # Start subprocess
    # Run a subprocess, capturing the output to a buffer whilst printing to the console

    # Create a pipe to capture the output
    pipe = io.StringIO()

    # Create a subprocess
    process = subprocess.Popen(
        subprocess_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    # Create a selector to listen for output
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)

    # Loop until the process has finished
    while process.poll() is None:
        # Wait for output
        for key, _ in selector.select():
            # Read output
            output = key.fileobj.readline()

            # Print output
            if process_line is not None:
                print(process_line(output), end = "")
            else:
                print(output, end = "")

            # Write output to buffer
            pipe.write(output)

    # read the pipe
    output = pipe.getvalue()

    # Close the pipe
    pipe.close()

    # Return the output
    return process.returncode == 0, output


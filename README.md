# Karton Playground: getting started

![](/uploads/upload_b7d8d61a76ba1cd8ec411d6b2a738cf9.png)

This is a repository that will help you get into Karton and create your own services immediately.

Karton is our distributed malware processing framework. If you don't know what it is and want to learn more, take a look at https://github.com/CERT-Polska/karton.

The remainder of this tutorial will assume that you at least voguely know what you want from Karton.

### List of services:

- `127.0.0.1:8030` karton-dashboard
- `127.0.0.1:8080` mwdb-core (user: admin, password: admin)
- `127.0.0.1:8090` minio (user: mwdb, password: mwdbmwdb)

### 1. Set up the playground

First, download, clone and run [the playground](http://link_do_githuba). This will create a friendly environment to help you get on your feet. Remember that it is not intend for production, but as a simple way to start your journey into the kartonverse.

```
git clone https://github.com/karton-playground
cd karton-playground
sudo docker-compose up  # this may take a while
```

That's it! A simple karton deployment is running on your local machine. Let's take a look around.

### 2. Click around

First, open the `mwdb-core` UI. This is the main interface for most of the users.

Open your browser and navigate to http://127.0.0.1:8080. You should see this:

![](/uploads/upload_75219ec442a89156f0801e11cfdb0fe2.png)

Now login with username `admin` and password `admin`. Volia, an empty malware database:

![](/uploads/upload_2088af2b5927b5928773648be95ff313.png)

But there is no malware yet. This is about to change. But first, check out the karton dashboard too. Navigate to http://127.0.0.1:8030 and see:

![](/uploads/upload_47c57a6d265998ce38140c007b4aca4d.png)

There's not a lot going on here. There are two karton services running - a classifier and a mwdb reporter. You can check out the queues, but understandably they're both empty.

And that's about it. There's also a minio interface available at http://127.0.0.1:8090 where all the samples, analysis artifact and temporary files live (login with `mwdb:mwdbmwdb`).

```
maybe mwdblib?

> ipython/jupyter :thinking_face: 
```

### 3. My first karton task

Let's play with karton. Right now, the tasks will pass right through the karton, becasue there is no "real work" going on. Let's create a simple Karton service to make things a bit more interesting. We will run `strings` on every incoming sample, and save the result into a new [TODO] in mwdb.

Go into the toplevel directory of the playground, and create a proper environemnt:

```bash
$ mkdir karton-strings
$ cp config/karton.local.ini karton-strings/karton.ini  # create a local config
$ cd karton-strings
$ python3 -m venv venv; source ./venv/bin/activate
$ pip install karton-core==4.0.4
$ vim karton-strings.py
```

Then copy or rewrite the following code into the opened file:

```python
from karton.core import Karton, Task, Resource
import subprocess


class Strings(Karton):
    """
    Runs the `strings` utility on incoming samples
    """

    identity = "karton.strings"
    filters = [{"type": "sample", "stage": "recognized"}]

    def process(self, task: Task) -> None:
        # Get the incoming sample
        sample_resource = task.get_resource("sample")

        # Log with self.log
        self.log.info(f"Hi {sample_resource.name}, let me analyse you!")

        # Download the resource to a temporary file
        with sample_resource.download_temporary_file() as sample_file:
            # And run `strings` on it
            strings = subprocess.check_output(["strings", sample_file.name])

        # Send our results for further processing or reporting
        task = Task(
            {"type": "sample", "stage": "analyzed"},
            payload={"parent": sample_resource, "sample": Resource("string", strings)},
        )
        self.send_task(task)


if __name__ == "__main__":
    # Here comes the main loop
    Strings().loop()

```

Doesn't look too complex, right?

### 4. Create your own karton

1. karton-boxjs


- Make the help tests silent


{
	"docbot_build": "rez_docbot build sphinx -- --source documentation/source --destination documentation/build",
	"docbot_publish": "rez_docbot publish github -- documentation/build",
}


- Add instructions on how to use test name constants, in Rez package.py files


Unittests
 - Exclude !package_requirement
 - Exclude ephemeral packages
 - Make sure requirements are found via `requires` as well as the test `requires`


## Adding Your Own Plugins
Adding your own plugins is easy.


### Builder Plugins
Create a file, name it anything you'd like.

TODO Finish this example

`example.py`
```python
import rez_docbot

class MyPlugin(rez_docbot):
	@staticmethod
	def get_name():
		return "my-plug-in"  # Note: Use this name in the CLI to call this plug-in

	def parse_arguments(text):
		parser = argparse.ArgumentParser(description="Add any arguments you'd like, here")
		parser.add_argument("--your", help="Some argument.")
		parser.add_argument("--arguments", help="Some argument.", choices=("bar", "another"))
		parser.add_argument("--here", help="Some argument.", actions="store_true")

		return parser.parse_args(text)

	def build(namespace):
		TODO


if __name__ == "__main__":
	rez_docbot.register_builder_plugin(MyPlugin)
```

Now add the path to your PYTHONPATH:

```bash
export PYTHONPATH=/some/folder:$PYTHONPATH
```

Make sure the module is accessible to Python before proceeding to the next step:


```bash
python -m example
python -m inner.folders.example  # If you added example.py to a folder like /some/folder/inner/folders/example.py
```

Lastly, add the path to the `REZ_DOCBOT_BUILDER_PLUGINS` environment variable

```bash
export REZ_DOCBOT_BUILDER_PLUGINS=inner.folders.example:$REZ_DOCBOT_BUILDER_PLUGINS
```

Now you're ready to use your plug-in.

```bash
rez_docbot build my-plug-in -- --your foo --arguments bar --here
```

In this case, "my-plug-in" was defined earlier, in `MyPlugin.get_name`.


### Publisher Plugins
TODO



## TODO
- Make sure builder / publisher plugins are cleaned up. e.g .
  clean up any empty strings.

 - Add a test for if there's only one build + publish pair
 - Add a test to allow multiple build + publish pairs

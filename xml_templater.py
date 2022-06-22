from typing import Any, Dict
from jinja2 import Environment, meta, FileSystemLoader, Template
import os


class XMLTemplate:

    def __init__(self, filename: str):
        self.filename = filename
        self.env = Environment(
            loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
            autoescape=True
        )

    @property
    def template(self) -> Template:
        return self.env.get_template(self.filename)

    def generate(self, **kwargs: Any) -> str:
        missing = set(self.get_kwargs()) - set(kwargs.keys())
        if len(missing) > 0:
            raise ValueError(f"Missing kwargs: {missing}")
        return self.template.render(**kwargs)

    def get_kwargs(self) -> Dict[str, Any]:
        with open(self.filename, "r") as f:
            source = f.read()
        parsed_content = self.env.parse(source)
        return {k: None for k in meta.find_undeclared_variables(parsed_content)}


if __name__ == "__main__":
    template = XMLTemplate("meta.xml.template")
    a = template.get_kwargs()
    print(template.generate(**a))



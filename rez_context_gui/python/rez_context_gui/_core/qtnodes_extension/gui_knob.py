import qtnodes

from .. import constant


class InputKnob(qtnodes.InputKnob):
    def __init__(self, *args, **kwargs):
        super(InputKnob, self).__init__(*args, **kwargs)

        self.name = constant.INPUT_NAME
        self.displayName = ""


class OutputKnob(qtnodes.OutputKnob):
    def __init__(self, *args, **kwargs):
        super(OutputKnob, self).__init__(*args, **kwargs)

        self.name = constant.OUTPUT_NAME
        self.displayName = ""

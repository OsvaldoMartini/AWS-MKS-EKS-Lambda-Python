## Installing and run Integration Tests  
### "pyyaml" package
```bash
  pip3 install -U -r .\back-end-python\gameactions\requirements.txt
```

### "Tests" Requeriments packages
```bash
  pip3 install -U -r .\back-end-python\tests\requirements.txt 
```

## Set ".Env" file for Environment Variables

```bash
  cd ./back-end-python/
  create file ".env"

  # Environment Variable

  AWS_SAN_STACK_NAME=trivia-app
```

## Setting the Test IDE Tests
### I need tyo Tell the IDE what tests we have

* Command Pallet <Ctlr + Shift + P>
* Search for "Python: Configure Tests
* Selecy "pytest" framework -> "tests" folder

## VsCode Pytest Configuration file
>settings.json
```bash

  # /.vscode/

  {
      "python.testing.pytestArgs": [
          "tests"
      ],
      "python.testing.unittestEnabled": false,
      "python.testing.nosetestsEnabled": false,
      "python.testing.pytestEnabled": true
  }
```


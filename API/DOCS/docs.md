# API DOCS

## ENPOINTS
- /uploadfile/
    - take JSON PAYLOAD {file in from  of form data} restrict file format to *.MOV
    ``` js
    
        function sendFile(url, formData) {
            document.getElementById('pstatus').textContent = ""
            var requestOptions = {
                method: 'POST',
                body: formData,
                redirect: 'follow'
            };
            fetch("http://0.0.0.0:8000/uploadfile/", requestOptions)
                .then((response) => {
                    response.json().then((data) => {
                        console.log(data)
                        document.getElementById('pstatus').textContent = "file processing..."
                        new Promise((res, rj) => {
                            status(data.id)
                        })
                    })

                })
            document.getElementById('pstatus').textContent = "file uploading..."

        }
    ```
    - output {"id": "9346fa95-d6a2-4067-a2f6-a59aeac127b3"} use this id in status endpoint for getting the status of file in server
- /status/
    - use status endpoint like this http://0.0.0.0:8000/status/{id}
    - it output a json response showing the status of file and its result ouput
    ``` JSON
    // NORMAL STAUS
    //
    {"out":None,"status":0,"message":"file start processing"}
    {"out":None,"status":1,"message":"file get resampled"}
    {"out":None,"status":2,"message":"file converted into spectrogram"}
    {"out":None,"status":3,"message":"data pre processing done"}
    {"out":None,"status":4,"message":"model processing the data"}
    // 0 means its real voice and 1 means its fake voice
    {"out":0/1,"status":5,"message":"model prediction"}
    
    // ERROR
    //
    // happend when voice duration higher than expected
    {"out":None,"status":-1,"message":"duration error"}
    // happend when file was not in write format
    {"out":None,"status":-2,"message":"file parse error"}
    ```

## SETTING UP THE DEV ENV
```bash
python3 -m venv env
```
### FOR WINDOWS
- STEP 1
  ```bash
   \env\Scripts\activate
  ```
- STEP 2
    ``` bash
    pip install -r requirements.txt
    ```
- STEP 3
    ```
    python3 app.py
    ```

### FOR LINUX
- STEP1
    ```bash
    . ./env/bin/avtivate
    ```
- STEP 2
    ``` bash
    pip install -r req.txt
    ```
- STEP 3
    ```
    python3 app.py
    ```
YOU CAN ACCESS THE API AT PORT 8000 or http://0.0.0.0:8000/{endpoints}
YOU CAN ACESS THE DOCS OF API BY doing to http://0.0.0.0:8000/docs here you can acess the API and use it fully
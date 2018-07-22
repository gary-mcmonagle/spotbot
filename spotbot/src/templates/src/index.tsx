import * as React from "react";
import * as ReactDOM from "react-dom";
import { Parent } from "./components/Parent";

//import { Track } from './components/Track';


var getUrl = window.location;
var baseUrl = getUrl .protocol + "//" + getUrl.host;
var dataEndpoint = baseUrl +  "/get_info"; 

ReactDOM.render(
    <div>
    <Parent dataEndpoint={dataEndpoint} refreshPeriod={10*1000}/>
    </div>,document.getElementById("Parent")
    
);

import * as React from "react";
import * as ReactDOM from "react-dom";
import { Parent } from "./components/Parent";

//import { Track } from './components/Track';



ReactDOM.render(
    <div>
    <Parent dataEndpoint="https://spotify-bot-gary.azurewebsites.net/get_info" refreshPeriod={10*1000}/>
    </div>,document.getElementById("Parent")
    
);

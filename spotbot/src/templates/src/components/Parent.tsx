import * as React from "react";

import { Track } from './Track';

export interface ParentProps {dataEndpoint: string;}

export class Parent extends React.Component<ParentProps, {}> {

    data:any = null;
    refreshData(dataEndpoint:string){
        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", dataEndpoint, false);
        xhttp.send();
        var response = JSON.parse(xhttp.responseText);
        console.log("-----------------------");
        console.log(response);
        console.log("-----------------------");
        this.data = response;
    }

    componentDidMount() {
        this.refreshData(this.props.dataEndpoint);
        setInterval(() => this.setState({ data: this.data}), 1000);
   }
    render() {
        this.refreshData(this.props.dataEndpoint);
        return 
        <Track track_title= {this.data.track_name} />
    }
}
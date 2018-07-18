import * as React from "react";

import { Track } from './Track';

export interface ParentProps {dataEndpoint: string; refreshPeriod:number;}

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
        setInterval(() => this.setState({ data: this.data}), this.props.refreshPeriod);
   }
    render() {
        this.refreshData(this.props.dataEndpoint);
        if(this.data.playlist_playing){
            return <div>
                <Track track_title ={this.data.track.title}
                album = {this.data.track.album}
                artist={this.data.track.artist}
                imageUrl = {this.data.track.image_url} />
            </div>
        }
        else{
            return <div><h1>Bot playlist not playing!!</h1></div> 
        }       
    }
}
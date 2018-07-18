import * as React from "react";

export interface TrackProps {track_title: string; artist:string; album:string;imageUrl:string}

// 'HelloProps' describes the shape of props.
// State is never set so we use the '{}' type.
export class Track extends React.Component<TrackProps, {}> {

    render() {
        return <div className="container">
            <div className="img">
            <img src={this.props.imageUrl} alt="Cheetah!" />
            </div>
            <div className="track-details">
            <h1>{this.props.track_title}</h1>
            <h2>Artist: {this.props.artist}</h2>
            <h2>Album: {this.props.album}</h2>
            </div>
            </div>;
    }
}
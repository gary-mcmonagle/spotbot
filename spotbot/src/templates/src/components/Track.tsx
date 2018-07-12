import * as React from "react";

export interface TrackProps {track_title: string;}

// 'HelloProps' describes the shape of props.
// State is never set so we use the '{}' type.
export class Child extends React.Component<TrackProps, {}> {
    render() {
        return <h1>Playing {this.props.track_title}</h1>;
    }
}
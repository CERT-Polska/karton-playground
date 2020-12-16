import React, {useState } from 'react';
import {connect} from 'react-redux';
import api from "@mwdb-web/commons/api"

function FirstAnalysisBanner(props) {
    const [submitted, setSubmitted] = useState(false)

    if(!props.isKartonManager || !props.attributes || props.object.type !== "file")
        return []

    if(Object.keys(props.attributes).some(
        label => props.attributes[label].some(
            attr => attr.key == "karton2"
        )
    ))
        return []

    let analyze = async (ev) => {
        ev.preventDefault();
        setSubmitted(true);
        await api.axios.post(`/karton/${props.object.id}`)
        // Update attributes
        props.onUpdateAttributes();
    }

    return (
        <div className="alert alert-primary">
            Oh! You've never run a Karton analysis for this sample.
            <button type="button" 
                    disabled={submitted}
                    className="btn-xs btn-primary float-right"
                    onClick={analyze}>
                Analyze!
            </button>
        </div>
    )
    
}


function mapStateToProps(state, ownProps) {
    return {
        ...ownProps,
        isKartonManager: state.auth.loggedUser.capabilities.includes("karton_manage"),
    }
}

export default connect(mapStateToProps)(FirstAnalysisBanner);

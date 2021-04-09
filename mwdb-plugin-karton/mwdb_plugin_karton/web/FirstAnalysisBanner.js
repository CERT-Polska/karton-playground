import React, { useContext, useState } from 'react';
import api from "@mwdb-web/commons/api";
import { AuthContext } from "@mwdb-web/commons/auth";

export default function FirstAnalysisBanner(props) {
    const [submitted, setSubmitted] = useState(false);
    const auth = useContext(AuthContext);
    const isKartonManager = auth.hasCapability("karton_manage");

    if(!isKartonManager || !props.attributes || props.object.type !== "file")
        return []

    if(Object.keys(props.attributes).some(
        label => props.attributes[label].some(
            attr => attr.key === "karton"
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

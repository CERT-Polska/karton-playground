import React, {useState, useEffect } from 'react';
import {connect} from 'react-redux';
import { Link } from 'react-router-dom';
import readableTime from 'readable-timestamp';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck, faCircleNotch, faSearch, faBan, faPlus } from '@fortawesome/free-solid-svg-icons'
import api from "@mwdb-web/commons/api"
import { makeSearchLink } from "@mwdb-web/commons/helpers";

function KartonAttributeRow(props) {
    const [status, setStatus] = useState();
    const [error, setError] = useState();

    useEffect(() => {
        let isMounted = true;
        if(props.uid && status == undefined)
        {
            api.axios.get(`/karton/${props.object.id}`, {
                params: {
                    root_uid: props.uid
                }
            }).then(response => {
                if(!isMounted)
                    return
                setStatus(response.data);
                // Completed tasks are not the running ones
                if(response.data.status !== "running")
                    props.onCompleted(props.uid)
            }).catch(error => {
                if(!isMounted)
                    return
                setError(error);
                // ... but failed ones are completed
                props.onCompleted(props.uid)
            })
        }
        // Invalidate component
        return () => { isMounted = false; }
    }, [status, props.uid])

    // If object has changed - reset status and error
    useEffect(() => {
        setStatus(undefined);
        setError(undefined);
    }, [props.uid])

    let queueStatusBadge = (queueStatus) => {
        let badgeStyle = queueStatus == "Started" ? "success" : "secondary";
        return (
            <span className={`badge badge-${badgeStyle}`} style={{marginRight: "8pt"}}>
                {queueStatus}
            </span>
        );
    };

    let analysisStatusBadge = (analysisStatus) => {
        console.log(analysisStatus);
        const badgeAttributes = ({
            [undefined]: {
                icon: faCircleNotch,
                style: "warning",
                message: "checking",
            },
            "error": {
                icon: faBan,
                style: "danger",
                message: "error",
            },
            "running": {
                icon: faCircleNotch,
                style: "warning",
                message: "processing",
            },
            "finished": {
                icon: faCheck,
                style: "success",
                message: "done",
            }
        })[analysisStatus];
        return (
            <span className={`badge badge-${badgeAttributes.style}`} style={{marginRight: "8pt"}}>
                <FontAwesomeIcon icon={badgeAttributes.icon} 
                                 pull="left"  
                                 spin={badgeAttributes.icon === faCircleNotch}/>
                {badgeAttributes.message}
            </span>
        );
    }

    let queueProcessingList = (
        <ul>
        {
            status && status["processing_in"]
            ? Object.keys(status["processing_in"]).map(queue => {
                let queueStatus = status["processing_in"][queue]
                return (
                    <li key={queue} className="text-monospace">
                        <div>
                            {queue}
                            {queueStatus["status"].map(queueStatusBadge)}
                        </div>
                        <div style={{fontSize: "x-small"}}>
                            got from{" "}
                            {
                                queueStatus["received_from"].join(", ")
                            }
                        </div>
                    </li>
                );
            }) : []
        }
        </ul>
    );

    let actionButtons = (
        <div>
            <Link to={makeSearchLink("meta.karton2", props.uid)}>
                <span className="badge badge-primary">
                    <FontAwesomeIcon icon={faSearch} pull="left" />
                    Search artifacts
                </span>
            </Link>
            {
                status && status["status"] == "running" && props.isKartonManager
                ? (
                    <a href={`https://karton.cert.pl/analysis/${props.uid}`}>
                        <span className="badge badge-primary">
                            <FontAwesomeIcon icon={faSearch} pull="left" />
                            Dashboard
                        </span>
                    </a>
                ): []
            }
            {
                props.isKartonManager 
                ? (
                    <a href={`https://buzz.cert.pl:8000/en-GB/app/search/karton_task_information?form.TASKUID=${props.uid}`}>
                        <span className="badge badge-primary">
                            <FontAwesomeIcon icon={faSearch} pull="left" />
                            Splunk logs
                        </span>
                    </a>
                ): []
            }
        </div>
    );

    return (
        <div className="card">
            <div className="card-header">
                <button className="btn btn-link dropdown-toggle" data-toggle="collapse" data-target={`#collapse${props.uid}`}>
                    {
                        analysisStatusBadge(
                            (error && "error") || (status && status["status"])
                        )
                    }
                    <span>{props.uid}</span>
                </button>
            </div>
            <div id={`collapse${props.uid}`} className="collapse">
                <div className="card-body">
                    {
                        error ? (
                            <div>
                                <b>Error:</b>{" "}
                                {(error.response && error.response.data.message) || error.toString()}
                            </div>
                        ) : []
                    }
                    {
                        status && status["last_update"] ? (
                            <div>
                                <b>Last update:</b>{" "}
                                {readableTime(new Date(parseFloat(status["last_update"]) * 1000))}
                            </div>
                        ) : []
                    }
                    {
                        status && status["processing_in"] ? (
                            <div>
                                <b>Currently processed by:</b>
                                {queueProcessingList}
                            </div>
                        ) : []
                    }
                    {actionButtons}
                </div>
            </div>
        </div>
    )
}

function KartonAttributeRenderer(props) {
    const [maxItems, setMaxItems] = useState(3);
    const [completedItems, setCompletedItems] = useState([]);
    const [visibleItems, setVisibleItems] = useState([]);
    const [canReanalyze, setCanReanalyze] = useState(false);

    useEffect(() => {
        setVisibleItems(props.values.slice(0, maxItems).map(attr => attr.value));
    }, [maxItems, props.values]);
    
    useEffect(() => {
        // User can reanalyze if all visible items are completed
        setCanReanalyze(
            !!visibleItems.length && 
            props.isKartonManager &&
            visibleItems.every(uid => completedItems.includes(uid)))
    }, [visibleItems, completedItems, props.isKartonManager])

    const submitAnalysis = async (ev) => {
        ev.preventDefault();
        // Turn off second reanalysis until we get new attribute state
        setCanReanalyze(false);
        // Trigger reanalysis
        await api.axios.post(`/karton/${props.object.id}`)
        // Update attributes
        props.onUpdateAttributes();
    }

    const showMore = (ev) => {
        ev.preventDefault();
        setMaxItems(maxItems + 3);
        setCanReanalyze(false);
    }

    let reanalyzeButton = (
        canReanalyze ? (
            <Link to="#" onClick={submitAnalysis}>
                <span className="badge badge-success">
                    <FontAwesomeIcon icon={faPlus} pull="left" />
                    reanalyze
                </span>
            </Link> 
        ) :
        (
            <span className="badge badge-muted">
                <FontAwesomeIcon icon={faPlus} pull="left" />
                reanalyze
            </span>
        )
    );

    let attributesRows = visibleItems.map(
        item => (
            <KartonAttributeRow key={item}
                                uid={item}
                                object={props.object}
                                isKartonManager={props.isKartonManager}
                                onCompleted={(uid) => {
                                    setCompletedItems(
                                        (completed) => completed.concat([uid])
                                    )
                                }}/>
        )
    )

    const isFileObject = props.object.type === "file";

    return (
        <tr key={props.label}>
            <th>
                {props.label}
            </th>
            <td>
                {attributesRows}
                {
                    maxItems < props.values.length 
                    ? (
                        <Link to="#" onClick={showMore}>
                            <span className="badge badge-primary">
                                more...
                            </span>
                        </Link>
                    ) : []
                }
                {
                    (props.isKartonManager && isFileObject) ? reanalyzeButton : []
                }
            </td>
        </tr>
    )
}

function mapStateToProps(state, ownProps)
{
    return {
        ...ownProps,
        isKartonManager: state.auth.loggedUser.capabilities.includes("karton_manage"),
    }
}

export default connect(mapStateToProps)(KartonAttributeRenderer);

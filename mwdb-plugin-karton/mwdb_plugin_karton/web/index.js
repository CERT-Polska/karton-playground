import KartonAttributeRenderer from "./KartonAttribute"
import FirstAnalysisBanner from "./FirstAnalysisBanner"


export default {
    attributeRenderers: {
        "karton": KartonAttributeRenderer
    },
    attributesListBefore: [
        FirstAnalysisBanner
    ],
    capabilities: [
        {
            "karton_manage": "Karton analysis management (analysis resubmission, access to dashboard)"
        }
    ]
}

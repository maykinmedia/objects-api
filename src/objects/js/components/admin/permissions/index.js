import React from "react"; 
import { createRoot } from "react-dom/client";

import { jsonScriptToVar } from "../../../utils";
import { PermissionForm } from "./permission-form";

const mount = () => {
    const node = document.getElementById('react-permissions');
    if (!node) return;

    const root = createRoot(node);
    root.render(
        <PermissionForm
            objectFields={jsonScriptToVar('object-fields')}
            tokenChoices={jsonScriptToVar('token-auth-choices')}
            objecttypeChoices={jsonScriptToVar('object-type-choices')}
            modeChoices={jsonScriptToVar('mode-choices')}
            formData={jsonScriptToVar('form-data')}
        />,
    );
};


mount();

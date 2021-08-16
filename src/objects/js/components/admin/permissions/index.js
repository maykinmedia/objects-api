import React from "react";
import ReactDOM from "react-dom";

import { PermissionForm } from "./permission-form";
import { jsonScriptToVar } from "../../../utils";

const mount = () => {
    const node = document.getElementById('react-permissions');
    if (!node) return;


    ReactDOM.render(
        <PermissionForm
            objectFields={jsonScriptToVar('object-fields')}
            dataFieldChoices={jsonScriptToVar('data-field-choices')}
            tokenChoices={jsonScriptToVar('token-auth-choices')}
            objecttypeChoices={jsonScriptToVar('object-type-choices')}
            modeChoices={jsonScriptToVar('mode-choices'}
            formData={jsonScriptToVar('form-data')}
        />,
        node
    );
};


mount();

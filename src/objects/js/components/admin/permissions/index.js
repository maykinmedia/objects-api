import React from "react";
import ReactDOM from "react-dom";

import { PermissionForm } from "./permission-form";
import { jsonScriptToVar } from "../../../utils";

const mount = () => {
    const node = document.getElementById('react-permissions');
    if (!node) return;

    const objectFields = jsonScriptToVar('object-fields');
    const dataFieldChoices = jsonScriptToVar('data-field-choices');
    const tokenChoices = jsonScriptToVar('token-auth-choices');
    const objecttypeChoices = jsonScriptToVar('object-type-choices');
    const modeChoices = jsonScriptToVar('mode-choices');
    const formData = jsonScriptToVar('form-data');

    ReactDOM.render(
        <PermissionForm
            objectFields={objectFields}
            dataFieldChoices={dataFieldChoices}
            tokenChoices={tokenChoices}
            objecttypeChoices={objecttypeChoices}
            modeChoices={modeChoices}
            formData={formData}
        />,
        node
    );
};


mount();

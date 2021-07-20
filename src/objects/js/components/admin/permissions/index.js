import React from "react";
import ReactDOM from "react-dom";

import { PermissionForm } from "./permission-form";
import { jsonScriptToVar } from "../../../utils";

const mount = () => {
    const node = document.getElementById('react-permissions');
    if (!node) return;

    const objectFields = jsonScriptToVar('object-fields');
    const dataFields = jsonScriptToVar('data-fields');
    const tokenChoices = jsonScriptToVar('token-auth-choices');
    const objecttypeChoices = jsonScriptToVar('object-type-choices');
    const modeChoices = jsonScriptToVar('mode-choices');

    console.log(objectFields);

    ReactDOM.render(
        <PermissionForm
            objectFields={objectFields}
            dataFields={dataFields}
            tokenChoices={tokenChoices}
            objecttypeChoices={objecttypeChoices}
            modeChoices={modeChoices}
        />,
        node
    );
};


mount();

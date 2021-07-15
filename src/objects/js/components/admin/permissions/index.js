import React from "react";
import ReactDOM from "react-dom";

import { PermissionForm } from "./permission-form";
import { jsonScriptToVar } from "../../../utils";

const mount = () => {
    const node = document.getElementById('react-permissions');
    if (!node) return;

    const objectFields = jsonScriptToVar('object-fields');
    const dataFields = jsonScriptToVar('data-fields');

    console.log(objectFields);

    ReactDOM.render(
        <PermissionForm objectFields={objectFields} dataFields={dataFields} />,
        node
    );
};


mount();

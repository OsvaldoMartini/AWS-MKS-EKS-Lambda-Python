import * as React from 'react';
import { createRoot } from 'react-dom/client';
import { createInstance, Piral, createStandardApi, PiletApi } from 'piral';
import { layout, errors } from './layout';
import { Link } from "react-router-dom";


const Page = React.lazy(() => import("./Page"));


// change to your feed URL here (either using feed.piral.cloud or your own service)
// const feedUrl = 'https://feed.piral.cloud/api/v1/pilet/empty';
const feedUrl = "https://feed.piral.cloud/api/v1/pilet/maindfedd";

export function setup(app: PiletApi) {
  app.registerTile(() => <Link to="/sample">Sample <b> Pilet</b>!</Link>, {
    initialColumns: 2,
    initialRows: 2,
  });
  app.registerPage("/sample", Page);
}

const instance = createInstance({
  state: {
    components: layout,
    errorComponents: errors,
  },
  plugins: [...createStandardApi()],
  requestPilets() {
    return fetch(feedUrl)
      .then((res) => res.json())
      .then((res) => res.items);
  },
});

const root = createRoot(document.querySelector('#app'));

root.render(<Piral instance={instance} />);

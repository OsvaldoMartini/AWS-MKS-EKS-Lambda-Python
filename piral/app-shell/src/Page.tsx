import * as React from 'react';

export default ({ data }) => (
  <div>
    <h1> My Page</h1>
    <p> this is justo some example</p>
    <ul>
      {data.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  </div>
)


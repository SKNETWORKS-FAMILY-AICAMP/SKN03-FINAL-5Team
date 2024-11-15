import { createElement, memo } from 'react';

export function reactContainer(useHook, view) {
  const Component = memo((props) => {
    const hookResult = useHook(props);
    return createElement(view, { ...hookResult });
  });

  Component.ViewComponent = view;
  Component.useHook = useHook;

  return Component;
}

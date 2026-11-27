import React from "react";
import { extrairIniciaisAvatar, obterCorAvatar } from "../../utils/avatarUtils";

interface UserAvatarProps {
  readonly nomeCompleto: string;
  readonly usuario: string;
  readonly size?: number;
  readonly bordered?: boolean;
}

export const UserAvatar: React.FC<UserAvatarProps> = ({
  nomeCompleto,
  usuario,
  size = 44,
  bordered = false,
}) => {
  const iniciais = extrairIniciaisAvatar(nomeCompleto, usuario);
  const backgroundColor = obterCorAvatar(usuario || nomeCompleto);
  const fontSize = Math.round(size * 0.37);

  return (
    <div
      aria-label={`Avatar de ${nomeCompleto || usuario}`}
      style={{
        width: size,
        height: size,
        backgroundColor,
        fontSize,
      }}
      className={`grid shrink-0 place-items-center rounded-full font-extrabold tracking-wide text-white select-none ${
        bordered ? "shadow-md" : "shadow-sm"
      }`}
    >
      {iniciais}
    </div>
  );
};

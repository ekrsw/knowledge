import React from 'react';
import { Edit, Trash2, ArrowLeft } from 'lucide-react';

interface PostTypeSelectionProps {
  onSelectModification: () => void;
  onSelectDeletion: () => void;
  onBack: () => void;
}

export const PostTypeSelection: React.FC<PostTypeSelectionProps> = ({
  onSelectModification,
  onSelectDeletion,
  onBack,
}) => {
  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="mr-2" size={20} />
            戻る
          </button>
          <h2 className="text-xl font-bold text-gray-900">投稿種別選択</h2>
        </div>
      </div>

      <div className="p-8">
        <div className="text-center mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            投稿の種別を選択してください
          </h3>
          <p className="text-gray-600">
            既存のFAQを修正するか、削除を提案するかを選択できます
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <div
            onClick={onSelectModification}
            className="group cursor-pointer bg-white border-2 border-gray-200 rounded-xl p-8 hover:border-gray-300 hover:shadow-lg transition-all duration-200"
          >
            <div className="text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-gray-200 transition-colors">
                <Edit className="text-gray-600 group-hover:text-gray-700" size={32} />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">修正案</h4>
              <p className="text-gray-600 leading-relaxed">
                既存のFAQの内容を修正・更新する提案を投稿します。
                新しい情報の追加や内容の改善を行えます。
              </p>
              <div className="mt-4 inline-flex items-center text-sm text-gray-500 group-hover:text-gray-600 transition-colors">
                <span>選択する</span>
                <ArrowLeft className="ml-2 rotate-180" size={16} />
              </div>
            </div>
          </div>

          <div
            onClick={onSelectDeletion}
            className="group cursor-pointer bg-white border-2 border-gray-200 rounded-xl p-8 hover:border-gray-300 hover:shadow-lg transition-all duration-200"
          >
            <div className="text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-gray-200 transition-colors">
                <Trash2 className="text-gray-600 group-hover:text-gray-700" size={32} />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">削除案</h4>
              <p className="text-gray-600 leading-relaxed">
                既存のFAQが不要になった場合や、
                内容が古くなった場合の削除を提案します。
              </p>
              <div className="mt-4 inline-flex items-center text-sm text-gray-500 group-hover:text-gray-600 transition-colors">
                <span>選択する</span>
                <ArrowLeft className="ml-2 rotate-180" size={16} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
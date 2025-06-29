import React, { useState } from 'react';
import { ArrowLeft, Trash2, X } from 'lucide-react';

interface DeleteProposalFormProps {
  onSubmit: (articleNumber: string, reason: string) => void;
  onCancel: () => void;
}

export const DeleteProposalForm: React.FC<DeleteProposalFormProps> = ({
  onSubmit,
  onCancel,
}) => {
  const [articleNumber, setArticleNumber] = useState('');
  const [reason, setReason] = useState('');
  const [errors, setErrors] = useState<{ articleNumber?: string; reason?: string }>({});

  const validateForm = () => {
    const newErrors: { articleNumber?: string; reason?: string } = {};

    if (!articleNumber.trim()) {
      newErrors.articleNumber = '記事番号を入力してください';
    } else if (!articleNumber.match(/^KBA-\d{5}-\d{5}$/)) {
      newErrors.articleNumber = '記事番号の形式が正しくありません（例: KBA-00001-12345）';
    }

    if (!reason.trim()) {
      newErrors.reason = '削除理由を入力してください';
    } else if (reason.trim().length < 10) {
      newErrors.reason = '削除理由は10文字以上で入力してください';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(articleNumber.trim(), reason.trim());
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <button
            onClick={onCancel}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="mr-2" size={20} />
            戻る
          </button>
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <Trash2 className="mr-2 text-red-600" size={24} />
            FAQ削除提案
          </h2>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-6">
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <Trash2 className="h-5 w-5 text-red-400 mt-0.5" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">削除提案について</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>
                  既存のFAQが不要になった場合や内容が古くなった場合に削除を提案できます。
                  削除提案は承認者による確認後に実行されます。
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <label htmlFor="articleNumber" className="block text-sm font-medium text-gray-700 mb-2">
              削除対象の記事番号 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="articleNumber"
              value={articleNumber}
              onChange={(e) => setArticleNumber(e.target.value)}
              placeholder="KBA-00001-12345"
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent transition-colors ${
                errors.articleNumber ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
            />
            {errors.articleNumber && (
              <p className="mt-1 text-sm text-red-600">{errors.articleNumber}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              削除したいFAQの記事番号を正確に入力してください
            </p>
          </div>

          <div>
            <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-2">
              削除理由 <span className="text-red-500">*</span>
            </label>
            <textarea
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={6}
              placeholder="削除が必要な理由を詳しく記入してください&#10;例：&#10;・情報が古くなり、現在の業務に適用できない&#10;・システム仕様変更により内容が不正確になった&#10;・類似のFAQが統合されたため重複している"
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent transition-colors resize-none ${
                errors.reason ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
            />
            {errors.reason && (
              <p className="mt-1 text-sm text-red-600">{errors.reason}</p>
            )}
            <div className="mt-1 flex justify-between text-xs text-gray-500">
              <span>削除理由は承認者が判断する重要な情報です</span>
              <span>{reason.length}/500文字</span>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200 bg-gray-50 -mx-6 px-6 -mb-6 pb-6">
          <div className="flex flex-col sm:flex-row gap-3 justify-end">
            <button
              type="button"
              onClick={onCancel}
              className="flex items-center justify-center px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              <X className="mr-2" size={18} />
              キャンセル
            </button>
            <button
              type="submit"
              className="flex items-center justify-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              <Trash2 className="mr-2" size={18} />
              削除提案を投稿
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};